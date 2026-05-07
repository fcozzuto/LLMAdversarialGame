def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in sorted(resources):
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Resource-denier: prefer spots we reach sooner; if tie, prefer denying (smaller od) and then farther from opponent.
        adv = od - sd
        key = (adv, -sd, -od, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                candidates.append((kdist(nx, ny, tx, ty), abs(dx) + abs(dy), dx, dy))
    if not candidates:
        return [0, 0]

    # Main: minimize distance to target; tie-break deterministically.
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(candidates[0][2]), int(candidates[0][3])]