# coding:utf-8
__autor__ = 'arachis'
__date__ = '2018/4/5'

'''
    Bi-RNN可以同时使用时序数据中某个输入的历史及未来数据。
    Bi-RNN网络结构的核心是把一个普通的单项的RNN拆成两个方向，一个随时序正向的，一个逆着时序的反向的
    本代码主要是使用Bidirectional LSTM Classifier对MNIST数据集上进行测试
'''

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets("../cnn/MNIST_data", one_hot=True)

# 设置对应的训练参数
learning_rate = 0.01
max_samples = 400000
batch_size = 128
display_step = 10

n_input = 28
n_steps = 28
n_hidden = 256
n_classes = 10

# 创建输入x和学习目标y的placeholder，
# 这里我们的样本被理解为一个时间序列，
# 第一个维度是时间点n_step，第二个维度是每个时间点的数据n_inpt。
# 同时，在最后创建Softmax层的权重和偏差
x = tf.placeholder("float", [None, n_steps, n_input])
y = tf.placeholder("float", [None, n_classes])

weights = tf.Variable(tf.random_normal([2 * n_hidden, n_classes]))
biases = tf.Variable(tf.random_normal([n_classes]))


def BiRNN(x, weights, biases):
    """
    定义Bidirectional LSTM网络的生成函数
    :param x:输入Tensor
    :param weights: 权重参数变量Tensor
    :param biases: 偏差参数变量Tensor
    :return: 输出变量Tensor
    """
    x = tf.transpose(x, [1, 0, 2])
    x = tf.reshape(x, [-1, n_input])
    x = tf.split(x, n_steps)

    lstm_fw_cell = tf.contrib.rnn.BasicLSTMCell(n_hidden, forget_bias=1.0)
    lstm_bw_cell = tf.contrib.rnn.BasicLSTMCell(n_hidden, forget_bias=1.0)

    outputs, _, _ = tf.contrib.rnn.static_bidirectional_rnn(lstm_fw_cell,
                                                            lstm_bw_cell, x,
                                                            dtype=tf.float32)
    return tf.matmul(outputs[-1], weights) + biases


# 使用tf.nn.softmax_cross_entropy_with_logits进行softmax处理并计算损失
pred = BiRNN(x, weights, biases)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

init = tf.global_variables_initializer()

# 开始执行训练和测试操作
with tf.Session() as sess:
    sess.run(init)
    step = 1
    while step * batch_size < max_samples:
        batch_x, batch_y = mnist.train.next_batch(batch_size)
        batch_x = batch_x.reshape((batch_size, n_steps, n_input))
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
        if step % display_step == 0:
            acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y})
            loss = sess.run(cost, feed_dict={x: batch_x, y: batch_y})
            print("Iter" + str(step * batch_size) + ", Minibatch Loss = " + \
                  "{:.6f}".format(loss) + ", Training Accuracy = " + \
                  "{:.5f}".format(acc))
        step += 1
    print("Optimization Finished!")

    test_len = 10000
    test_data = mnist.test.images[:test_len].reshape((-1, n_steps, n_input))
    test_label = mnist.test.labels[:test_len]
    print("Testing Accuracy:", sess.run(accuracy, feed_dict={x: test_data, y: test_label}))
