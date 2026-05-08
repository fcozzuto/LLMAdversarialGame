def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in role) or ("chaser" in role) or (role == "pursuer")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        mdx = nx - ox
        mdy = ny - oy
        dsq = mdx * mdx + mdy * mdy

        # Wall-run-ish bias: prefer moves that keep moving along the dominant direction,
        # while slightly discouraging "killing" motion when that would collide with walls (handled by valid()).
        step_dom = abs(mdx) + abs(mdy)
        align = 0
        if step_dom != 0:
            # Encourage reducing the larger component toward pursuer / keeping it away for evader.
            if abs(mdx) >= abs(mdy):
                align = -1 if (mdx > 0 and pursuer) or (mdx < 0 and pursuer) else (1 if not pursuer else -1)
            else:
                align = -1 if (mdy > 0 and pursuer) or (mdy < 0 and pursuer) else (1 if not pursuer else -1)

        if pursuer:
            score = (-dsq * 100) + (-abs(mdx) * 3) + (-abs(mdy) * 3) + align
        else:
            score = (dsq * 100) + (-abs(mdx) * 1) + (-abs(mdy) * 1) + align

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]