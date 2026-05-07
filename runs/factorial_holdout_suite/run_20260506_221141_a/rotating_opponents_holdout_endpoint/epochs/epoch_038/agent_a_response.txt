def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_turns = int(observation.get("turns_remaining", 0) or 0)
    near_bonus = 6 if my_turns < 15 else 4
    block_bonus = 2 if my_turns < 25 else 1
    edge_pen = 1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        step_val = -edge_pen * (1 if nx in (0, w-1) or ny in (0, h-1) else 0)
        found_now = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                found_now = 1
                break
        if found_now:
            return [dx, dy]

        local_best = -10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            grab_rate = (d_opp - d_self)  # positive means we are closer than opponent
            value = 10 * grab_rate - 2 * d_self
            if d_self == 1:
                value += near_bonus
            local_best = value if value > local_best else local_best

        if (nx, ny) in obstacles:
            step_val -= 50
        else:
            step_val += local_best
            if abs(nx - ox) + abs(ny - oy) <= 2:
                step_val += block_bonus  # crowd opponent when tied

        if step_val > best_val:
            best_val = step_val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]