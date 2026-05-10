def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def best_for(targetx, targety, maximize):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(nx - targetx) + abs(ny - targety)
            val = dist if maximize else -dist
            if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
                best = (val, (dx, dy))
        return best[1] if best is not None else (0, 0)

    if role == "evader":
        tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
        ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
        return list(best_for(tx, ty, True))

    vx, vy = ox - sx, oy - sy
    step_x = 0 if vx == 0 else (1 if vx > 0 else -1)
    step_y = 0 if vy == 0 else (1 if vy > 0 else -1)
    targetx = clamp(ox + step_x, 0, w - 1)
    targety = clamp(oy + step_y, 0, h - 1)
    return list(best_for(targetx, targety, False))