def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0, 10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
                continue
            d1 = manh(nx, ny, tx, ty)
            d2 = manh(nx, ny, ox, oy)
            if (d1, d2) < (best[2], best[3]):
                best = (dx, dy, d1, d2)
        return [best[0], best[1]]

    # Choose move that goes toward the resource where we have the best "advantage" over opponent.
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        # Compute best advantage among remaining resources if we are at (nx, ny)
        best_adv = -10**18
        best_dist = 10**9
        for rx, ry in resources:
            ds = manh(nx, ny, rx, ry)
            do = manh(ox, oy, rx, ry)
            # Prefer resources we can reach first; also prefer closer targets to prevent dithering.
            adv = (do - ds)
            # Slight tie-break to reduce path length
            if adv > best_adv or (adv == best_adv and ds < best_dist):
                best_adv = adv
                best_dist = ds

        # Encourage progress and discourage letting opponent get closer to the chosen advantage target.
        # The opponent-closing term uses global best_adv approximation via do-ds behavior.
        opp_term = 0
        if best_adv != -10**18:
            # If best_adv is negative, we're likely losing that target; reduce score further.
            opp_term = -abs(best_adv) * 0.25

        score = best_adv * 10.0 - best_dist + opp_term
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]