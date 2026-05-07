def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Prefer resources where we can beat the opponent in arrival time; otherwise, reduce the gap.
    best = None
    for (rx, ry) in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - self_d  # positive is good for us
        # Tie-break: closer to pick up soon, then deterministic by coordinates
        key = (adv, -self_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    rx, ry = best[1]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_step = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = man(nx, ny, rx, ry)
        d_opp_to_target = man(ox, oy, rx, ry)
        # Small deterministic preference to keep progressing
        step_key = (d_to_target, abs((nx - rx)) + abs((ny - ry)), -dx, -dy)
        if best_score is None or step_key < best_score:
            best_score = step_key
            best_step = [dx, dy]

    # If all neighboring cells are blocked, stay still.
    return best_step if best_step is not None else [0, 0]