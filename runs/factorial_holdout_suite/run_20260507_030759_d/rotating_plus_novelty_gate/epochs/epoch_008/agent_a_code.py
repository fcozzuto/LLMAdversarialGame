def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; break ties by being closer, then farther from opponent.
        key = (sd - od, sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Greedy step toward target with deterministic obstacle avoidance and contest awareness.
    best_step = None
    best_step_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nds = dist(nx, ny, tx, ty)
        nod = dist(ox, oy, tx, ty)
        # Keep our distance decreasing; also discourage stepping into cells that make us lose the contest.
        key = (nds + 2 * max(0, nds - nod), nds, abs(nx - ox) + abs(ny - oy), -nx, -ny)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]