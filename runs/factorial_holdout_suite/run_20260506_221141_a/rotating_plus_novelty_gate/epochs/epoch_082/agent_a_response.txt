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

    def mhd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_val = -10**18
    # Deterministic iteration order
    resources.sort()
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Prefer resources we can get sooner than opponent; if contested, still favor largest lead.
        val = (od - sd) * 1000 - sd
        # Small deterministic tie-break: prefer nearer and then lexicographically smaller resource
        val += -((rx + ry) // 1000)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    # Prefer moves that reduce our distance; if tie, prefer increasing opponent distance and stability deterministically.
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        nsd = mhd(nx, ny, tx, ty)
        nod = mhd(ox, oy, tx, ty)
        # nudges: favor reducing our distance strongly; slight preference for making it harder for opponent (via sd lead)
        score = -(nsd * 1000) + (nod - nsd) * 10
        # Deterministic tie-break: smaller delta lexicographically
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]