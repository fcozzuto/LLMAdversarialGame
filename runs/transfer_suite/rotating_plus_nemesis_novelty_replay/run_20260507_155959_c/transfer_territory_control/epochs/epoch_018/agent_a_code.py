def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) or [0, 0])[:2]
    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    unclaimed = observation.get("unclaimed_cells", []) or []
    if not unclaimed:
        return [0, 0]

    self_territory = observation.get("self_territory", []) or []
    opp_territory = observation.get("opponent_territory", []) or []
    self_cells = [tuple(xy) for xy in self_territory if isinstance(xy, (list, tuple)) and len(xy) >= 2]
    opp_cells = [tuple(xy) for xy in opp_territory if isinstance(xy, (list, tuple)) and len(xy) >= 2]

    if opp_cells:
        ax = sum(x for x, _ in opp_cells) // len(opp_cells)
        ay = sum(y for _, y in opp_cells) // len(opp_cells)
    else:
        ax, ay = ox, oy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer unclaimed cells close to us, but also closer to opponent's territory center (counterclaim).
    # Deterministic tie-breaking by lexicographic coordinates.
    best = None
    best_key = None
    for x, y in unclaimed:
        x = int(x); y = int(y)
        if not inb(x, y) or (x, y) in obstacles:
            continue
        if self_cells:
            d_us = min(manh(x, y, px, py) for px, py in self_cells)
        else:
            d_us = manh(x, y, sx, sy)
        d_opp = manh(x, y, ax, ay)
        # Combine: closeness to us dominates; slight preference toward opponent.
        key = (d_us, -d_opp, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the straight greedy step lands on an obstacle, try a reduced movement deterministically.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles or not inb(nx, ny):
        if dy != 0 and (sx, sy + dy) not in obstacles and inb(sx, sy + dy):
            return [0, dy]
        if dx != 0 and (sx + dx, sy) not in obstacles and inb(sx + dx, sy):
            return [dx, 0]
        return [0, 0]

    return [dx, dy]