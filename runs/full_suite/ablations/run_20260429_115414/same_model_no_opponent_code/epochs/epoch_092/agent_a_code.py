def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    # Target selection: prefer resources where we are closer than opponent; otherwise minimize advantage gap.
    target = None
    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        advantage = do - ds  # positive means we are closer
        # Add secondary tie-break: prefer near center-ish and lower remaining risk of being contested.
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        contested_pen = 0.0
        if do <= ds:
            contested_pen = 0.5 + 0.1 * (ds - do)
        key = (-(advantage - contested_pen), ds, center_bias)
        if best is None or key < best:
            best = key
            target = (rx, ry)

    # If no resources, move to reduce distance to opponent's corner direction (deterministic fallback).
    if target is None:
        tx, ty = (0 if ox > sx else w - 1), (0 if oy > sy else h - 1)
    else:
        tx, ty = target

    # Choose move that greedily improves approach to target and avoids becoming closer for opponent.
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = dist(nx, ny, tx, ty)
        do_next = dist(nx, ny, ox, oy)
        # Also discourage stepping away from target.
        toward_score = ds_next
        # Opponent-avoidance: prefer squares that keep us not too close to opponent while contesting.
        opp_score = do_next
        # Deterministic ordering already from dirs; use tuple key.
        key = (toward_score, -opp_score, nx, ny)
        cand.append((key, (dx, dy)))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda z: z[0])
    return [int(cand[0][1][0]), int(cand[0][1][1])]