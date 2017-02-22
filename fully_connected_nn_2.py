# TODO PEP-8 import
from nn_2_layers import *

BATCH_SIZE = 128
MAX_STEPS = 9001


def run_training(training_rate, train_dataset, train_labels, valid_dataset, valid_labels, test_dataset, test_labels,
                 reg_beta):

    # Build the graph
    graph = tf.Graph()
    with graph.as_default():

        # Input data. For the training data, we use a placeholder that will be fed
        # at run time with a training minibatch.
        tf_train_dataset = tf.placeholder(tf.float32,
                                          shape=(BATCH_SIZE, IMAGE_PIXELS))
        tf_train_labels = tf.placeholder(tf.float32, shape=(BATCH_SIZE, NUM_LABELS))
        tf_valid_dataset = tf.constant(valid_dataset)
        tf_test_dataset = tf.constant(test_dataset)
        global_step = tf.Variable(0)

        # Variables.
        variables = inference(tf_train_dataset)

        # Training computation.
        loss_op = loss(tf_train_labels, variables, reg_beta)

        # Optimizer.
        learning_rate = tf.train.exponential_decay(training_rate, global_step, 1000, 0.65, staircase=True)
        train_op = training(loss_op, learning_rate, global_step)

        # Predictions for the training, validation, and test data.
        train_prediction, valid_prediction, test_prediction = prediction(tf_valid_dataset,
                                                                         tf_test_dataset, variables)

    with tf.Session(graph=graph) as sess:
        # Init handler
        init = tf.global_variables_initializer()

        # Run the Op to initialize the variables.
        sess.run(init)

        for step in range(MAX_STEPS):
            offset = (step * BATCH_SIZE) % (train_labels.shape[0] - BATCH_SIZE)

            # Generate a mini batch
            batch_data = train_dataset[offset:(offset + BATCH_SIZE), :]
            batch_labels = train_labels[offset:(offset + BATCH_SIZE), :]

            # Prepare a dictionary telling the session where to feed the minibatch.
            # The key of the dictionary is the placeholder node of the graph to be fed,
            # and the value is the numpy array to feed to it.
            feed_dict = {
                tf_train_dataset: batch_data,
                tf_train_labels: batch_labels
            }
            _, loss_value, predictions = sess.run([train_op, loss_op, train_prediction], feed_dict=feed_dict)

            if step % 500 == 0:
                print('{} {}: {}'.format('NN 2 Layers loss at step', step, loss_value))
                print('{}: {}'.format('NN 2 Layers Accuracy', evaluation(predictions, batch_labels)))
                print('{}: {}'.format('NN 2 Layers Validation Accuracy',
                                      evaluation(valid_prediction.eval(), valid_labels)))

        print('{}: {}'.format('NN 2 Layers Test Accuracy', evaluation(test_prediction.eval(), test_labels)))
