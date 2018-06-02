
from sklearn.mixture import GaussianMixture

NUMBER_OF_PEOPLE = 30 # 278 # this is huge...

# TODO: as for now this really sucks, optimise parameters / data / features / algorithm

def train_gmm(features, labels):
    gmm = GaussianMixture(n_components=NUMBER_OF_PEOPLE,  covariance_type='full', n_init=10, warm_start=True, verbose=1)
    gmm.fit(features, labels)
    return gmm

if __name__ == "__main__":
    from AplikacjaTestowa.DataPreparation.load_data import get_data
    from AplikacjaTestowa.FeatureExtraction.mfcc import calculate_mfcc

    train, test = get_data()
    Xtrain, Ytrain = calculate_mfcc(train, verbose=True)
    Xtest, Ytest = calculate_mfcc(test, verbose=True)

    gmm = train_gmm(Xtrain, Ytrain)
    naive_preds = gmm.predict(Xtrain)
    predictions = gmm.predict(Xtest)

    print('naive')
    print(naive_preds == Ytrain)
    print(naive_preds)
    print(sum(naive_preds == Ytrain)/len(Ytrain))
    print('\n\n\n\n')

    print('actual')
    print(predictions == Ytest)
    print(sum(predictions == Ytest)/len(Ytest))