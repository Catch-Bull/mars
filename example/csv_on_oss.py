import os
import mars
import mars.tensor as mt
import mars.dataframe as md
from mars.dataframe.datastore.to_csv import to_csv
from mars.dataframe.datasource.read_csv import read_csv
from mars.lib.filesystem import open_file, glob


def get_oss_auth_path(file_path):
    from mars.lib.filesystem.oss import build_oss_path

    access_key_id = os.environ["OSS_KEY_ID"]
    access_key_secret = os.environ["OSS_KEY_SECRET"]
    end_point = os.environ["ENDPOINT"]
    auth_path = build_oss_path(file_path, access_key_id, access_key_secret, end_point)
    return auth_path


if __name__ == "__main__":
    oss_path = get_oss_auth_path("oss://bucket/key/test_write.txt")

    with open_file(oss_path, "w") as f:
        for i in range(20):
            f.write(f"oss write test {i}\n")

    with open_file(oss_path, "rb") as f:
        data = f.read()
        print("data:\n", data.decode("utf-8"))

    session = mars.new_session(default=True)

    oss_path = get_oss_auth_path(
        "oss://bucket/key/test_mars_csv_*.csv"
    )

    data = mt.random.random((10000, 5))
    data = md.DataFrame(data, columns=list("abcde"), chunk_size=(1000, 1)).execute()

    res = to_csv(data, oss_path)
    res.execute()

    res = []
    for path in glob(oss_path):
        print("read path:", path)
        res.append(read_csv(path))
    res = md.concat(res).execute()
    from IPython import embed

    embed()
