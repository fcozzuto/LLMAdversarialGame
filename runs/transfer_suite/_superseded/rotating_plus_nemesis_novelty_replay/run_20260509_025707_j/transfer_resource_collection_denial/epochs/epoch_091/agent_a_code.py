def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    tr = observation.get("turns_remaining", 0)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    bestv = -10**18

    # Switch behavior late game: prioritize shorter my path (secure remaining) instead of contesting.
    late = tr <= 8

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Find resource that maximizes estimated advantage vs nearest-resource opponent.
        # Advantage = (opponent arrival slack) primarily; tie-break on my speed and safety.
        best_adv = -10**18
        best_my_d = 10**9
        for r in resources:
            rx, ry = r[0], r[1]
            myd = d(nx, ny, rx, ry)
            oppd = d(ox, oy, rx, ry)
            slack = oppd - myd  # positive means we are closer next turn
            # Secondary: prefer closer targets for earlier claim; add small bonus for bigger slack.
            if late:
                val = -myd + 0.15 * slack
            else:
                val = slack * 10 - myd * 0.7
            if val > best_adv or (val == best_adv and myd < best_my_d):
                best_adv = val
                best_my_d = myd

        # Safety: avoid moving adjacent to obstacles if it doesn't help (reduce getting stuck).
        # Deterministic micro-penalty.
        danger = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                    danger += 1
        v = best_adv - 0.2 * danger

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best