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

    tr = int(observation.get("turns_remaining", 0) or 0)
    rem = int(observation.get("remaining_resource_count", 0) or 0)

    best = None
    best_val = -10**18
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        if sd == 0:
            return [0, 0]
        # Prefer resources we can reach earlier; break ties by making it awkward for opponent (far + row pressure).
        val = (od - sd) * 120
        val += (1 if ry == oy else 0) * 15  # contest on opponent's current row
        val += (1 if rx == ox else 0) * 8   # also contest aligned column
        val += (0 if (sd > (tr + 1)) else 20)  # only if reachable soon
        val -= od * 2                          # farther from opponent is better
        val += (1 if rem <= 4 else 0) * (od - sd)  # near end, prioritize lead
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in blocked:
                continue
            candidates.append((mhd(nx, ny, tx, ty), (dx, dy), (nx, ny) == (tx, ty)))

    # Prefer steps that reduce distance; if equal, prefer aligning row/col progress toward target; then deterministic tie-break.
    candidates.sort(key=lambda t: (t[0], -int(t[2]), abs((sx + t[1][0]) - tx) + abs((sy + t[1][1]) - ty), t[1][0], t[1][1]))
    return list(candidates[0][1])