def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose target resource: prioritize those we are not worse than opponent on; else best potential swing.
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        if sd <= od:
            val = -sd + 0.7 * (od - sd)  # strong preference to resources we can secure
        else:
            val = - (sd - od)  # still pursue if we can reduce the disadvantage
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    # If no resources, move to reduce opponent distance slightly (deny).
    if best_t is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    cur_to_t = abs(tx - sx) + abs(ty - sy)
    cur_to_o = abs(ox - sx) + abs(oy - sy)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nt = abs(tx - nx) + abs(ty - ny)
        no = abs(ox - nx) + abs(oy - ny)

        # Progress toward target and "deny" by increasing opponent distance.
        prog = cur_to_t - nt
        deny = no - cur_to_o

        # Interception pressure: prefer moves that improve our advantage over opponent to the same target.
        us_adv_before = (cur_to_t - cur_to_o)
        us_adv_after = (nt - no)
        swing = us_adv_before - us_adv_after

        # Tie-breakers: avoid stepping into squares that are closer to obstacles poorly (local penalty).
        local_block_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obs:
                    local_block_pen += 1

        score = 5.0 * prog + 1.2 * deny + 2.0 * swing - 0.05 * local_block_pen
        # Deterministic tie-break: prefer smaller (dx,dy) lexicographically after score.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]