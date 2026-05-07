def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # If no resources, drift toward center avoiding obstacles
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]
        # fallback: any safe move toward center
        best = None
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    d = cheb(nx, ny, tx, ty)
                    if best is None or d < best[0] or (d == best[0] and (ddx, ddy) < best[1]):
                        best = (d, (ddx, ddy))
        return list(best[1]) if best else [0, 0]

    # Choose resource maximizing lead over opponent; break ties by farther-from-opponent and then coordinates
    best = None
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        lead = od - sd  # positive means we can reach sooner or tie favorably
        # Prefer cells where we can secure earlier; also avoid giving opponent easy access by penalizing small od
        key = (lead, -od, sd, x, y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    _, (tx, ty) = best

    # Move toward target with obstacle-aware best next step
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
    cand = (desired_dx, desired_dy)

    nx, ny = sx + cand[0], sy + cand[1]
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
        return [cand[0], cand[1]]

    best_next = None
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                d_to = cheb(nx, ny, tx, ty)
                # secondary: maintain lead vs opponent if possible
                od_next = cheb(ox, oy, tx, ty)
                sd_next = d_to
                lead = od_next - sd_next
                key = (lead, -od_next, -sd_next, (ddx, ddy))
                if best_next is None or key > best_next[0]:
                    best_next = (key, (ddx, ddy))
    return list(best_next[1]) if best_next else [0, 0]