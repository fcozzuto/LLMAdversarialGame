def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells") or []
    uset = []
    for p in unclaimed:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            uset.append((p[0], p[1]))

    opp_terr = observation.get("opponent_territory") or []
    opset = set()
    for p in opp_terr:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opset.add((p[0], p[1]))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaker: lowest dx, then lowest dy (via fixed move order above)
    best = (0, 0)
    best_sc = -10**18

    # If no unclaimed, still move to pressure center while keeping away from obstacles
    if not uset:
        uset = []

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in oset:
            continue

        d_center = dist(nx, ny, cx, cy)
        d_opp = dist(nx, ny, ox, oy)

        # Prefer moving toward the nearest unclaimed if it exists; otherwise toward center.
        if uset:
            d_un = 10**9
            for tx, ty in uset:
                d = dist(nx, ny, tx, ty)
                if d < d_un:
                    d_un = d
        else:
            d_un = d_center

        # Risk model: entering opponent territory can flip; but if that is likely bad, avoid it.
        # Use a conservative penalty proportional to closeness to opponent.
        in_opponent = 1 if (nx, ny) in opset else 0

        sc = 0
        # Higher score is better:
        sc += 80.0 / (1.0 + d_un)          # claim potential
        sc += 35.0 / (1.0 + d_center)      # center control
        sc += 18.0 * (d_opp) / (1.0 + d_opp)  # generally stay farther unless it conflicts
        sc -= 120.0 * in_opponent * (1.0 / (1.0 + d_opp))  # avoid risky flips
        # Small preference to keep moving (avoid staying still unless it is best)
        sc -= 0.5 * (dx == 0 and dy == 0)

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]