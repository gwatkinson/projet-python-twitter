### Import les modules ###
import pytest
import tweepy
import projet_python_twitter.streaming as stream
import projet_python_twitter.listes_mots as listes
import projet_python_twitter.project_errors as errors


@pytest.fixture
def file_credentials():
    """Returns the dictionary in projet_python_twitter._credentials"""
    try:
        import projet_python_twitter._credentials

        return projet_python_twitter._credentials.credentials
    except ModuleNotFoundError as e:
        print(
            "Erreur : " + str(e),
            "",
            "Vérifier que '_credentials.py' existe bien et est dans le bon dossier ('projet_python_twitter/')",
            sep="\n",
        )
        return None


def test_file_cred(file_credentials):
    """Test que les clés nécessaires sont bien dans '_credentials.py'"""
    print(file_credentials)
    assert all(
        key in file_credentials
        for key in [
            "consumer_key",
            "consumer_secret",
            "access_token",
            "access_token_secret",
        ]
    )


def test_credentials_type():
    """Test qu'une erreur est levée quand credentials n'est pas un dictionnaire"""
    with pytest.raises(errors.CredentialsType):
        stream.credentials_class(credentials="XXXXXXXXX")


def test_custom_cred_missing():
    """Test qu'une erreur est levée si les credentials données ne sont pas complets"""
    with pytest.raises(errors.MissingKey):
        stream.credentials_class(
            credentials={
                "consumer_key": "",
                "consumer_secret": "",
                "access_token": "",
                "az": 40,
            }
        )


def test_custom_cred_type():
    """Test qu'une erreur est levée si les credentials données ne sont pas complets"""
    with pytest.raises(errors.CredentialsKeyType):
        stream.credentials_class(
            credentials={
                "consumer_key": "",
                "consumer_secret": 3,
                "access_token": "",
                "access_token_secret": "",
            }
        )


# def test_init_cred():
#     """Test si la classe s'initialise bien"""
#     cred = stream.credentials_class(
#         credentials={
#             "consumer_key": "XXX",
#             "consumer_secret": "XXX",
#             "access_token": "XXX",
#             "access_token_secret": "XXX",
#         }
#     )
#     with pytest.raises(tweepy.TweepError):
#         # Récupère la time_line des authentifiants
#         # Renvoie une erreur s'ils sont incorrects
#         cred.api.user_timeline(page=1)


def test_cred_SListener():
    """Test qu'une erreur est levée si 'credentials' n'est pas une instance de 'credentials_class'"""
    with pytest.raises(errors.CredentialsClassType):
        stream.SListener(
            credentials={
                "consumer_key": "XXX",
                "consumer_secret": "XXX",
                "access_token": "XXX",
                "access_token_secret": "XXX",
            }
        )


def test_word_start_stream():
    """Test qu'une erreur est levée si 'credentials' n'est pas une instance de 'credentials_class'"""
    with pytest.raises(errors.WordType):
        stream.start_stream(
            liste_mots=[3, True, "AAA"],
            credentials=stream.credentials_class(
                credentials={
                    "consumer_key": "XXX",
                    "consumer_secret": "XXX",
                    "access_token": "XXX",
                    "access_token_secret": "XXX",
                }
            ),
        )


def test_cred_start_stream():
    """Test qu'une erreur est levée si 'credentials' n'est pas une instance de 'credentials_class'"""
    with pytest.raises(errors.CredentialsClassType):
        stream.start_stream(
            liste_mots=["AAA", "BBB"],
            credentials={
                "consumer_key": "XXX",
                "consumer_secret": "XXX",
                "access_token": "XXX",
                "access_token_secret": "XXX",
            },
        )
