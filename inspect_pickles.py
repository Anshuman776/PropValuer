import os
import pickle
import traceback


def inspect_pickles(path='.'):
    files = sorted(os.listdir(path))
    pkls = [f for f in files if f.endswith('.pkl')]

    print('CWD:', os.path.abspath(path))
    print('Files in folder:')
    for f in files:
        if f.endswith(('.pkl', '.ipynb', '.csv')):
            print('  ', f)

    if not pkls:
        print('\nNo .pkl files found.')
        return

    for fname in pkls:
        print('\n---', fname)
        full = os.path.join(path, fname)
        try:
            with open(full, 'rb') as fh:
                obj = pickle.load(fh)
        except Exception:
            print('  Could not unpickle:', fname)
            traceback.print_exc()
            continue

        print('  type:', type(obj))
        # Common attrs
        for attr in ('n_features_in_', 'feature_names_in_'):
            val = getattr(obj, attr, None)
            if val is not None:
                print(f'  {attr}:', val)

        # If it's a SearchCV-like, show best_estimator_
        if hasattr(obj, 'best_estimator_'):
            be = obj.best_estimator_
            print('  is SearchCV, best_estimator type:', type(be))
            for attr in ('n_features_in_', 'feature_names_in_'):
                val = getattr(be, attr, None)
                if val is not None:
                    print(f'    best_estimator_.{attr}:', val)

        # If it's a Pipeline, show steps
        if hasattr(obj, 'steps'):
            print('  Pipeline steps:')
            for name, step in obj.steps:
                print('   -', name, type(step))

    print('\nDone.')


if __name__ == '__main__':
    inspect_pickles('.')
