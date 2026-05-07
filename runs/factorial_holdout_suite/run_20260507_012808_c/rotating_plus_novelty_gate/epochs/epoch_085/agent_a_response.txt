def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: prefer resources we can reach no later than opponent; otherwise, reduce the opponent's lead.
    best = None
    for (rx, ry) in resources:
        self_d = md(sx, sy, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        adv = opp_d - self_d  # positive => we are closer
        can_take = 1 if self_d <= opp_d else 0
        # Higher can_take first, then higher adv, then smaller self_d, then deterministic tie-break.
        key = (can_take, adv, -self_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Step towards target with simple deterministic obstacle-aware greedy.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best_delta = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        hit = (nx, ny) in obstacles
        # Prefer non-hit moves that reduce distance to target; slight penalty for staying still.
        dist = md(nx, ny, tx, ty)
        score = (-int(hit), -dist, -int(dx == 0 and dy == 0), -abs((tx - nx) - (sx - tx)))
        if best_score is None or score > best_score:
            best_score = score
            best_delta = (dx, dy)

    return [int(best_delta[0]), int(best_delta[1])]