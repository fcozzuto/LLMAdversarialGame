def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_target = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat, else contest those with smallest disadvantage
        key = (od - sd, sd, -abs(rx - ox) - abs(ry - oy), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    best_val = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if best_target is None:
            val = -(cheb(nx, ny, ox, oy))  # just avoid getting too close; deterministic
        else:
            sd = cheb(nx, ny, tx, ty)
            cur_sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Move closer to target and prefer states where we are ahead or the opponent isn't
            lead_now = cur_sd - od
            lead_next = sd - od
            # Encourage progress (reduce distance), and penalize giving opponent better access to nearby resources
            val = (lead_next, sd, -lead_now, rx_bias) if False else None
            # Nearby-opponent/resource pressure (small, deterministic sample)
            pressure = 0
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d <= 3:
                    od2 = cheb(ox, oy, rx, ry)
                    # if opponent is closer to a nearby resource than we are, count pressure
                    if od2 < d:
                        pressure += 1
                    elif od2 == d:
                        pressure += 0.5
            progress = sd
            val = (lead_next * 10 + progress) + pressure * 0.25

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]