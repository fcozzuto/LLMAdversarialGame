def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # Deterministic safe drift: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Favor targets we can reach first; slight bias for same row/col as opponent to contest.
        contest = 0
        if ry == oy:
            contest += 1
        if rx == ox:
            contest += 0.5
        # Add small tie-break toward closer targets to reduce dithering.
        key = (-(do - ds + contest), ds + 0.1 * (rx + 2 * ry), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        ds_next = abs(tx - nx) + abs(ty - ny)
        do_cur = abs(tx - ox) + abs(ty - oy)
        # Want to keep advantage over opponent for target; also avoid enabling opponent pickup:
        # if we are far behind, prioritize moves that increase distance between us and opponent in Manhattan,
        # otherwise prioritize reaching target quickly.
        adv_next = do_cur - ds_next
        dist_us_opp = abs(nx - ox) + abs(ny - oy)

        # Secondary: prefer moves that move along shortest path direction to the target.
        step_prog = -((abs(tx - nx) + abs(ty - ny)) - (abs(tx - sx) + abs(ty - sy)))

        # Small deterministic preference ordering encoded in tuple.
        key = (-(adv_next), ds_next + 0.02 * dist_us_opp - 0.1 * step_prog, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]