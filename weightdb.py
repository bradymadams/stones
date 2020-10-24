#! /usr/bin/env python

import sys
import sqlite3
import datetime
import shutil

class WeightDb(object):
    DBName = 'weight.db'

    def __init__(self, name=DBName):
        self.name = name
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def backup(self):
        shutil.copyfile(self.name, self.name + '.bak')

    def create_table(self):
        self.cursor.execute('CREATE TABLE weight_history (date datetime, weight real)')
        self.conn.commit()

    def add_weight(self, weight, when=None):
        if when is None:
            when = datetime.datetime.now()

        self.cursor.execute('INSERT INTO weight_history (date, weight) VALUES(?, ?)', (when, float(weight)))
        self.conn.commit()

    def add_csvdump(self, csv):
        csvf = open(csv, 'r')
        rows = csvf.readlines()
        csvf.close()

        for r in rows:
            d, t, v = r.split(',')
            dt = datetime.datetime.strptime(d + ' ' + t, '%m/%d/%y %I:%M:%S %p')
            self.add_weight(float(v), dt)

    def get_weights(self, days=None):
        select = 'SELECT * FROM weight_history'
        args = []
        if days:
            select += ' WHERE date > ?'
            oldest = datetime.datetime.now() - datetime.timedelta(days=days)
            args.append(oldest)

        select += ' ORDER BY date DESC'

        nrows = self.cursor.execute(select, args)

        return nrows.fetchall()

class WeightHistory(object):
    def __init__(self, db, days):
        self.weights = db.get_weights(days)

    def count(self):
        return len(self.weights)

    def average(self):
        if self.count() == 0:
            return 0.0
        return sum(weight for when, weight in self.weights) / float(len(self.weights))

    def minimum(self):
        if self.count() == 0:
            return 0.0
        return min(weight for when, weight in self.weights)

    def maximum(self):
        if self.count() == 0:
            return 0.0
        return max(weight for when, weight in self.weights)

    def dict_all(self):
        return {
            'weights': self.weights,
            'average': '%6.2f' % self.average(),
            'minimum': '%6.2f' % self.minimum(),
            'maximum': '%6.2f' % self.maximum()
        }

def usage():
    print('%s -OPTION VALUE' % sys.argv[0])
    print('Options:')
    print('a --> Add weight VALUE')

def main():
    if len(sys.argv) < 3:
        usage()
        sys.exit(0)

    w = WeightDb()

    if sys.argv[1] == '-a':
        w.backup()
        v = float(sys.argv[2])
        w.add_weight(v)
    else:
        usage()

    w.close()

if __name__ == '__main__':
    main()

