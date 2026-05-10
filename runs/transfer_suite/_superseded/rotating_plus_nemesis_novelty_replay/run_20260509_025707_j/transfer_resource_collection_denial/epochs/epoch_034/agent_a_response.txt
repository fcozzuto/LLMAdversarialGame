def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list if p is not None and len(p) >= 2}
    resources = observation.get("resources", []) or []

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (0, 0)
    best_key = None
    if resources:
        # For each move, pick the resource that gives best "reach advantage" this turn.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            best_for_move = None
            for r in resources:
                if r is None or len(r) < 2:
                    continue
                rx, ry = r[0], r[1]
                if not ok(rx, ry):
                    continue
                myd = md(nx, ny, rx, ry)
                opd = md(ox, oy, rx, ry)
                adv = opd - myd  # positive => I can reach no later than opponent
                # Prefer positive adv; then prefer smaller myd; then deterministic tie-break by resource coord.
                key = (adv, -myd, -rx, -ry)
                if best_for_move is None or key > best_for_move:
                    best_for_move = key
            if best_for_move is None:
                key2 = (-10**9, 0, 0, 0)
            else:
                key2 = best_for_move
            # Deterministic overall tie-break: resource advantage, then my distance, then direction.
            overall = (key2[0], key2[1], key2[2], key2[3], dx, dy)
            if best_key is None or overall > best_key:
                best_key = overall
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]