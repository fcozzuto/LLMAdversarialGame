def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    unclaimed = set()
    for key in ("unclaimed_cells", "resources"):
        v = observation.get(key, None)
        if isinstance(v, list) and v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    unclaimed.add((int(p[0]), int(p[1])))
            if key == "unclaimed_cells":
                break

    self_terr = set()
    for p in observation.get("self_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_terr.add((int(p[0]), int(p[1])))

    opp_terr = set()
    for p in observation.get("opponent_territory", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    ox, oy = int(ox), int(oy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # adjacency to our territory (and not obstacle)
    neigh = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        sc = 0
        sc += -dist(nx, ny, cx, cy)  # prefer central control
        sc += 0.4 * (dist(sx, sy, ox, oy) - dist(nx, ny, ox, oy))  # drift away from opponent
        if (nx, ny) in unclaimed:
            sc += 6.0 + 0.2 * min(dist(nx, ny, cx, cy), w + h)
        if (nx, ny) in opp_terr:
            sc += 2.0  # allow counterclaim when it helps central pressure
        if (nx, ny) in self_terr:
            sc += 0.8
        for ax, ay in neigh:
            px, py = nx + ax, ny + ay
            if (px, py) in self_terr:
                sc += 3.0
                break
        if best is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)
    return [int(best[0]), int(best[1])]