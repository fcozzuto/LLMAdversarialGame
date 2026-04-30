def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not (w and h):
        return [0, 0]

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    # Consider up to 6 closest resources to keep it fast and stable.
    if resources:
        rs = []
        for r in resources:
            rx, ry = r[0], r[1]
            rs.append((dist(sx, sy, rx, ry), rx, ry, dist(ox, oy, rx, ry)))
        rs.sort(key=lambda x: x[0])
        rs = rs[:6]
    else:
        rs = []

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        if not rs:
            val = -abs(nx - sx) - abs(ny - sy)
        else:
            val = 0
            for _, rx, ry, do in rs:
                dn = dist(nx, ny, rx, ry)
                gain = do - dn
                if gain > 0:
                    val += 10 * gain
                else:
                    val += gain
            # Mild tie-break: prefer moving towards nearest resource.
            if rs:
                _, rx0, ry0, _ = rs[0]
                val += -dist(nx, ny, rx0, ry0)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]