def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    edge_opp = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)

    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = man(x, y, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # positive => we're closer
        edge_res = (rx == 0 or rx == w - 1 or ry == 0 or ry == h - 1)
        key = (
            1 if advantage >= 0 else 0,
            advantage + (3 if edge_opp and edge_res else 0),
            -od,
            -sd
        )
        if best_key is None or key > best_key:
            best_key, best_res = key, (rx, ry)

    tx, ty = best_res

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    # Additional bias: if opponent is very close to the target, try to block by moving toward it more directly.
    opp_close = man(ox, oy, tx, ty) <= 2

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        # Prefer reducing distance to target, and when advantageous, keep opponent farther from the same target.
        score = (-d_self, (d_opp - d_self) if d_self <= man(x, y, tx, ty) else (-(d_self)), 0)
        if edge_opp:
            score = (score[0] + (-1 if (tx == 0 or tx == w - 1) and (nx == 0 or nx == w - 1) else 0),
                     score[1] + (1 if (tx == nx or ty == ny) else 0),
                     1 if opp_close else 0)
        # Tie-breakers: avoid stepping into positions where staying closer to target is worse than current.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]