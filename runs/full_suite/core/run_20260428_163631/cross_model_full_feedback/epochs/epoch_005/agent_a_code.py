def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        best = None
        best_key = None
        for r in resources:
            if r in obstacles:
                continue
            d_me = man((sx, sy), r)
            d_opp = man((ox, oy), r)
            key = (d_opp - d_me, -d_opp, r[0], r[1])
            if best_key is None or key > best_key:
                best_key = key
                best = r
        return best if best is not None else (w // 2, h // 2)

    target = best_target()

    def neighbors_free(pos):
        x, y = pos
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    best_move = (0, 0)
    best_val = None
    cur_on_resource = (sx, sy) in set(resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d_me = man((nx, ny), target)
        d_opp = man((ox, oy), target)

        # Reward collecting and reducing opponent's advantage
        val = 0
        if (nx, ny) in resources:
            val += 1000
        val += (d_opp - d_me) * 10
        val += -d_me  # still progress
        val += (neighbors_free((nx, ny)) - neighbors_free((sx, sy))) * 2

        # If opponent is significantly closer to current target, gently bias to other resources
        if resources and d_opp + 1 < d_me:
            alt_best_key = None
            alt_best_val = None
            for r in resources:
                if r in obstacles:
                    continue
                ad_me = man((nx, ny), r)
                ad_opp = man((ox, oy), r)
                akey = (ad_opp - ad_me, -ad_me, r[0], r[1])
                if alt_best_key is None or akey > alt_best_key:
                    alt_best_key = akey
                    alt_best_val = (ad_opp - ad_me)
            val += alt_best_val * 6 if alt_best_val is not None else 0

        if best_val is None or val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    # If already on a resource, consider staying to avoid losing turn progress deterministically
    if cur_on_resource and best_move != (0, 0):
        return [0, 0]
    return [best_move[0], best_move[1]]