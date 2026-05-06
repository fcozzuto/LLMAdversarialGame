def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a target where we can beat opponent (otherwise pick best available race).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Strong preference for winning races; slight central bias; small tie-break by coordinate.
        key = ((-1 if sd < od else 1) * (abs(od - sd) + (1.0 / (sd + 1))) + (0.02 * (-abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0))), -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = man(nx, ny, rx, ry)
        opp_d = man(ox, oy, rx, ry)

        # Step toward target, but also slow opponent: prefer moves that reduce opponent's next advantage.
        # Deterministic local opponent "greed" estimate: where opponent would step if chasing this target.
        od_moves = []
        for pdx, pdy in moves:
            px, py = ox + pdx, oy + pdy
            if not (0 <= px < w and 0 <= py < h) or (px, py) in obstacles:
                continue
            od_moves.append((pdx, pdy, man(px, py, rx, ry)))
        if od_moves:
            od_moves.sort(key=lambda t: (t[2], t[0], t[1]))
            next_opp_d = od_moves[0][2]
        else:
            next_opp_d = opp_d

        # Occupying cells near resources is good; avoid drifting away.
        dist_change = (man(sx, sy, rx, ry) - my_d)

        # Mild obstacle-gap behavior: if both axes blocked, staying can be better.
        blocked = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            tx, ty = nx + adx, ny + ady
            if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obstacles:
                blocked += 1

        val = 4.0 * dist_change + (1.0 / (my_d + 1)) - (1.2 / (next_opp_d + 1)) - 0.03 * my_d - 0.02 * blocked
        if best_val is None or val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]