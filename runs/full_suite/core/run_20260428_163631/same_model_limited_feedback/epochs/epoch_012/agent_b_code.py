def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    best_mv = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in set(tuple(r) for r in resources):
            sc += 100000
        if resources:
            d_self = min(man(nx, ny, r[0], r[1]) for r in resources)
            d_opp = min(man(ox, oy, r[0], r[1]) for r in resources)
            sc += (d_opp - d_self) * 100 - d_self
        if observation.get("scores"):
            try:
                sc += int(observation["scores"][0]) - int(observation["scores"][1])
            except:
                pass
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = [dx, dy]
    return best_mv