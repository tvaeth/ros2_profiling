import numpy as np

from ros2profile.data.event_sequence import EventSequence
from ros2profile.data import build_graph

def test_sequence(profile_events):
    events = profile_events
    graph  = build_graph(events)

    malloc = event_data['lttng_ust_libc:malloc']
    calloc = event_data['lttng_ust_libc:calloc']
    realloc = event_data['lttng_ust_libc:realloc']
    free = event_data['lttng_ust_libc:free']
    memalign = event_data['lttng_ust_libc:memalign']
    posix_memalign = event_data['lttng_ust_libc:posix_memalign']

    def filter_sequence(sequence, start, end, cpu):
        return filter(lambda x: x['_timestamp'] >= start and x['_timestamp'] <= end and x['cpu_id'] == cpu, sequence)

    def check_sequence(event_sequence, callback_event_sequence):
        events_in_callback_sequence = len(list(event_sequence)) > 0
        
        if events_in_callback_sequence:
            sorted_sequence = sorted(event_sequence, key=lambda x: x['_timestamp'])

            for event in sorted_sequence :
                callback_event_sequence.append({
                    'node': 'task_manager',
                    'event': event['_name'],
                    'topic': 'N/A',
                    'timestamp': event['_timestamp']
                })
        
        return not events_in_callback_sequence
            

    node = graph.node_by_name('task_manager')
    event_seq = EventSequence(node.subscriptions[1].callback.events()[0])

    extended_seq = []

    for sub in node.subscriptions:
        callback_events = sub.callback.events()
        
        if not callback_events:
            continue
            
        for callback_sequence in callback_events:
            seq = EventSequence(callback_sequence)
            sorted_event_seq = sorted(seq.sequence, key=lambda x: x['timestamp'])

            node_cpu  = seq.cpu_id
            seq_start = sorted_event_seq[0]['timestamp']
            seq_end   = sorted_event_seq[-1]['timestamp']
            
            extended_event_seq = sorted_event_seq.copy()
            init_length = len(extended_event_seq)

            malloc_seq = filter_sequence(malloc, seq_start, seq_end, node_cpu)
            assert check_sequence(malloc_seq, extended_event_seq) 
                
            calloc_seq = filter_sequence(calloc, seq_start, seq_end, node_cpu)
            assert check_sequence(calloc_seq, extended_event_seq)         

            realloc_seq = filter_sequence(realloc, seq_start, seq_end, node_cpu)
            assert check_sequence(realloc_seq, extended_event_seq) 

            free_seq = filter_sequence(free, seq_start, seq_end, node_cpu)
            assert check_sequence(free_seq, extended_event_seq) 

            memalign_seq = filter_sequence(memalign, seq_start, seq_end, node_cpu)
            assert check_sequence(memalign_seq, extended_event_seq) 

            posix_memalign_seq = filter_sequence(posix_memalign, seq_start, seq_end, node_cpu)
            assert check_sequence(posix_memalign_seq, extended_event_seq) 
            
            if init_length < len(extended_event_seq):
                extended_seq.append(sorted(extended_event_seq, key=lambda x: x['timestamp']))
