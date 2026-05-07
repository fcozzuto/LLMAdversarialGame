def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            cell = (int(r[0]), int(r[1]))
            if cell not in obstacles:
                resources.append(cell)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # For each move, evaluate immediate advantage using the best resource for us,
    # but incorporate how "contested" it is by the opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # self_contest considers the best resource for us under (opp_dist - self_dist)
        best_self = -10**18
        best_self_d = None
        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prioritize winning the next collection by reaching earlier; penalize moves that
            # still leave opponent too close (contested).
            v = (do - ds) * 1000 - ds
            if v > best_self or (v == best_self and (best_self_d is None or ds < best_self_d)):
                best_self = v
                best_self_d = ds

        # Small tie-break: also prefer moves that reduce our closest-to-any-resource distance.
        closest_self = min(man(nx, ny, tx, ty) for tx, ty in resources)

        # Opponent pressure: if our move lets opponent have a much easier time to the nearest resource they can access,
        # we slightly discount it (using current positions, since we can't predict reliably).
        closest_opp = min(man(ox, oy, tx, ty) for tx, ty in resources)
        val = best_self - closest_self + (closest_opp * 0.1)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]