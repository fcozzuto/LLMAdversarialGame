def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = (None, -10**18)
    if is_evader:
        far_corner = max(corners, key=lambda c: (man(c[0], c[1], ox, oy), -(abs(c[0] - sx) + abs(c[1] - sy)), c[0] * 17 + c[1]))
        cx, cy = far_corner
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            corner_drive = -man(nx, ny, cx, cy)
            tie = -(man(nx, ny, sx, sy) * 0.001)  # slight prefer movement reduction
            sc = d * 100 + corner_drive + tie
            if sc > best[1] or (sc == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), sc)
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            corner_clamp = 0
            if (nx, ny) == (ox, oy):
                sc = 10**12
            else:
                corner_clamp = 0.001 * (min(nx, w - 1 - nx) + min(ny, h - 1 - ny))  # mild center bias
                sc = (-d) * 1000 + corner_clamp + (-(abs(dx) + abs(dy)) * 0.01)
            if sc > best[1] or (sc == best[1] and (dx, dy) < best[0]):
                best = ((dx, dy), sc)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]