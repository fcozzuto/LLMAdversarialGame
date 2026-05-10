def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    # If opponent is likely to deny, prefer resources where we are closer (or will become closer).
    def d2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    candidates = []
    for r in resources:
        my_d = d2(my_pos, r)
        opp_d = d2(opp_pos, r)
        # Higher score means better advantage and proximity.
        # Subtract a term to discourage far resources even if advantage exists.
        adv = (opp_d - my_d)
        score = adv * 10 - (my_d // 1)
        candidates.append((score, r, my_d, opp_d))
    candidates.sort(key=lambda x: (x[0], -x[2]), reverse=True)
    top_targets = [c[1] for c in candidates[:6]]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Also avoid walking next to opponent if we don't have an advantageous target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        npos = (nx, ny)

        # Evaluate best target for this move.
        val = -10**18
        for tx, ty in top_targets:
            t = (tx, ty)
            my_d = d2(npos, t)
            opp_d = d2(opp_pos, t)
            adv = (opp_d - my_d)
            # Encourage immediate progress and deny risk.
            immediate = -my_d
            risk = d2(npos, opp_pos)
            v = adv * 10 + immediate - (risk // 2)
            # If we can get on top of a target quickly, prioritize strongly.
            v += 20000 // (1 + my_d)
            val = max(val, v)

        # Micro-tie-break: prefer moves that reduce distance to current best target.
        if val == best_val:
            # deterministic preference order already; keep first found
            pass

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]