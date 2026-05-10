def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obs_prox(x, y):
        if not obstacles:
            return 99
        md = 10**9
        for ax, ay in obs_set:
            d = abs(ax - x) + abs(ay - y)
            if d < md:
                md = d
                if md <= 1:
                    break
        return md

    def mobility(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    best = None
    best_val = -10**18 if role == "pursuer" else -10**18

    # When pursuer: maximize (closer to opponent). When evader: maximize (farther from opponent).
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        d = man((nx, ny), (ox, oy))
        mp = mobility(nx, ny)
        prox = obs_prox(nx, ny)

        if role == "pursuer":
            val = (-d * 10.0) + (mp * 0.6) + (prox * 0.1)
            # Slight bias to reduce zigzag space: prefer staying on same general row/col.
            val += (0.25 if nx == ox else 0.0) + (0.25 if ny == oy else 0.0)
        else:
            val = (d * 10.0) + (mp * 0.8) + (prox * 0.1)
            # Avoid hugging obstacles while evading.
            if prox <= 1:
                val -= 5.0

        if best is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]