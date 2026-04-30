def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        res = [(w // 2, h // 2)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    t = int(observation.get("turn_index", 0))

    # Deterministic tie-breaking preference order rotated by turn parity.
    rot = t % 9
    order = moves[rot:] + moves[:rot]

    best = (0, 0)
    best_val = -10**18

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        self_to_opp = man(nx, ny, ox, oy)

        # Score: prioritize resources where we can be competitive vs opponent.
        val = -10**9
        for rx, ry in res:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Want small ds; prefer resources where we are not much worse than opponent.
            # Small additional incentive to reduce distance to opponent only when similar.
            v = (-ds * 3.0) + ((do - ds) * 1.5) - (self_to_opp * 0.02)
            # Break ties deterministically by coordinates.
            v += (-(rx + 1) * 0.001 - (ry + 1) * 0.0001)
            if v > val:
                val = v
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]