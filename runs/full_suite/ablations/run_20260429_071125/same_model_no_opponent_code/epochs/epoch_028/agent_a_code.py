def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    occ = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                occ.add((px, py))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in occ:
                resources.append((rx, ry))

    deltas = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)
    def center_score(px, py):
        return -(abs(px - (w - 1) / 2.0) + abs(py - (h - 1) / 2.0))

    best_move = (0, 0)
    best_val = -10**18

    if resources:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not safe(nx, ny):
                continue
            val = -10**18
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                # Prefer moves that improve your lead on a resource, then break ties by safety/center
                cand = (od - sd) * 1000 - sd + center_score(nx, ny) + (-(man(nx, ny, ox, oy)))
                if cand > val:
                    val = cand
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not safe(nx, ny):
                continue
            val = center_score(nx, ny) - man(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]