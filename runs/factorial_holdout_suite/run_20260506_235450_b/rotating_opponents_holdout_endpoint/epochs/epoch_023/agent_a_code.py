def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                x, y = int(a["x"]), int(a["y"])
                obs_set.add((x, y))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            obs_set.add((int(a[0]), int(a[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs_set:
            resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (score, our_dist, dx, dy)

    def mhn(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        # Evaluate move by best achievable advantage on any resource.
        move_best_score = None
        for rx, ry in resources:
            our_d = mhn(nx, ny, rx, ry)
            opp_d = mhn(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier; lightly penalize contested ones.
            score = (opp_d - our_d) * 100 - (our_d if our_d <= opp_d else our_d + 5)
            # Encourage being able to secure at least one resource quickly.
            if our_d == 0:
                score += 10000
            if move_best_score is None or score > move_best_score[0] or (score == move_best_score[0] and our_d < move_best_score[1]):
                move_best_score = (score, our_d)

        if move_best_score is None:
            continue

        cand = (move_best_score[0], move_best_score[1], dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[2]), int(best[3])]