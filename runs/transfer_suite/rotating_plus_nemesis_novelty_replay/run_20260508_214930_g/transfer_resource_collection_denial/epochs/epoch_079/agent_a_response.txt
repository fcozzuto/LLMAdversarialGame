def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    # Select a target that we can reach earlier than the opponent (denial pressure).
    best_target = resources[0]
    best_gap = -10**9
    best_self_d = 10**9
    for tx, ty in resources:
        d_self = dist(sx, sy, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        gap = d_opp - d_self
        if gap > best_gap or (gap == best_gap and d_self < best_self_d):
            best_gap = gap
            best_self_d = d_self
            best_target = (tx, ty)

    tx, ty = best_target

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_self_next = dist(nx, ny, tx, ty)
        d_opp_to_target = dist(ox, oy, tx, ty)
        landed = 1 if (nx, ny) in res_set else 0

        # Encourage immediate collection; otherwise, get closer while maintaining denier advantage.
        score = landed * 1000 - d_self_next * 5 + (d_opp_to_target - d_self_next) * 2

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move