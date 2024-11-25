import unittest
import os
from video_clip import extract_audio_from_url, root_directory
import requests

class TestExtractAudioFromUrl(unittest.TestCase):
    def setUp(self):
        """测试前的设置"""
        # 确保临时目录存在
        os.makedirs(f"{root_directory}/tmp", exist_ok=True)

    # def tearDown(self):
    #     """测试后的清理"""
    #     # 清理临时文件
    #     for file in os.listdir(f"{root_directory}/tmp"):
    #         if file.startswith("temp_media_"):
    #             os.remove(os.path.join(f"{root_directory}/tmp", file))

    def test_extract_audio_from_video_url(self):
        """测试从视频URL提取音频"""
        # 使用更可靠的测试URL
        test_url = "https://cn-hljheb-ct-01-04.bilivideo.com/upgcxcode/15/15/757021515/757021515-1-16.mp4?e=ig8euxZM2rNcNbRVhwdVhwdlhWdVhwdVhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1731929017&gen=playurlv2&os=cosbv&oi=24503444&trid=b8c319dda27b4934b97d2ac6bc2617edh&mid=0&platform=html5&og=cos&upsig=316333974f94be584399312bbcbda945&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform,og&bvc=vod&nettype=0&f=h_0_0&bw=54348&logo=80000000"  # 替换为可用的测试URL
        
        try:
            result = extract_audio_from_url(test_url)
            # 验证结果是否为音频文件
            self.assertTrue(result.endswith('.wav') or result.endswith('.mp3'))
            self.assertTrue(os.path.exists(result))
        except requests.exceptions.RequestException as e:
            self.skipTest(f"网络错误，跳过测试: {str(e)}")
        except Exception as e:
            self.fail(f"测试失败，出现异常: {str(e)}")

if __name__ == '__main__':
    unittest.main() 