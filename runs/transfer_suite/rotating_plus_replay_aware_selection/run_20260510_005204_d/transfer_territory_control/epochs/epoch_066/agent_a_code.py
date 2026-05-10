def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))
    if len(unclaimed) > 30:
        unclaimed = sorted(unclaimed, key=lambda c: max(abs(c[0]-sx), abs(c[1]-sy)))[:30]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    unclaimed_set = set(unclaimed)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        d_claim = 0
        if unclaimed:
            d_claim = min(cheb(nx, ny, cx, cy) for (cx, cy) in unclaimed)
        gain = 1 if (nx, ny) in unclaimed_set else 0
        # Prefer: higher gain, higher distance to opponent, lower distance to unclaimed, then deterministic tie-break
        key = (-(gain), -(d_opp), d_claim, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]