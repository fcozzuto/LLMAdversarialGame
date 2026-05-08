def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for t in observation.get("obstacles", []) or []:
        if isinstance(t, (list, tuple)) and len(t) == 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for t in observation.get("resources", []) or []:
        if isinstance(t, (list, tuple)) and len(t) == 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx >= dy else dy  # Chebyshev for 8-neighbor moves

    def best_score_for(pos_self, pos_opp):
        # predicts opponent as nearest_resource under same metric (deterministic tie-break),
        # then chooses our target preferring resources we can reach sooner.
        opp_nearest = None
        best_opp = None
        for r in sorted(resources):
            d = dist(pos_opp, r)
            key = (d, r[0], r[1])
            if best_opp is None or key < best_opp:
                best_opp = key
                opp_nearest = r
        # Score resources by advantage in reach time over opponent's nearest (fallback to all resources).
        best = None
        for r in sorted(resources):
            ds = dist(pos_self, r)
            do = dist(pos_opp, r)
            # primary: how much earlier we arrive than opponent; secondary: closer.
            key = (do - ds, -ds, -((r[0] - opp_nearest[0]) ** 2 + (r[1] - opp_nearest[1]) ** 2), r[0], r[1])
            if best is None or key > best:
                best = key
        return best

    # choose actual move by maximizing best_score_for at next self position
    best_move = (None, None)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        key = best_score_for((nx, ny), (ox, oy))
        if key is None:
            continue
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    # if all moves blocked, stay
    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]