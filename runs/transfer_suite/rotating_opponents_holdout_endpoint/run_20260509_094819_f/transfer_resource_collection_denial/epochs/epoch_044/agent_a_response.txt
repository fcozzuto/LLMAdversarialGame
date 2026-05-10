def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
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

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_tval = None
    for rx, ry in resources:
        our_d = manh(sx, sy, rx, ry)
        opp_d = manh(ox, oy, rx, ry)
        if our_d == 0:
            tval = 10**9
        else:
            tval = (opp_d - our_d) * 1000 - our_d
        if best_tval is None or tval > best_tval or (tval == best_tval and (rx, ry) < best_target):
            best_tval = tval
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        our_d2 = manh(nx, ny, tx, ty)

        # Secondary tie-break: keep pressure by improving our lead on the target;
        # also slightly avoid giving opponent a quick capture path to our next position.
        opp_d2 = manh(ox, oy, tx, ty)
        val = (opp_d2 - our_d2) * 1000 - our_d2

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]