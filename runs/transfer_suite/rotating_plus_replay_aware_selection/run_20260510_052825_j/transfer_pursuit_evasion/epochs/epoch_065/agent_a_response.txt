def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    self_role = observation.get("self_role", "pursuer")
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Heuristic target: for pursuer, chase opponent; for evader, run from pursuer.
    tx, ty = (ox, oy) if self_role != "evader" else (ox, oy)

    # If evader and resources exist, bias away from pursuer while also not walking onto resource-adjacent traps.
    # (Resources are scarce; keep it simple.)
    if self_role != "evader" and resources:
        # Prefer nearest resource if it reduces distance to opponent via detour heuristic.
        best = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if valid(rx, ry):
                    cur = max(abs(sx - ox), abs(sy - oy))
                    det = max(abs(rx - ox), abs(ry - oy))
                    score = det * 2 + ((sx - rx) * (sx - rx) + (sy - ry) * (sy - ry))
                    if best is None or score < best[0]:
                        best = (score, rx, ry)
        if best is not None:
            tx, ty = best[1], best[2]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    if self_role == "evader":
        best_val = None  # maximize distance to pursuer
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = max(abs(nx - ox), abs(ny - oy))  # Chebyshev
            # Small bias to keep to edges/corners (corner evasion archetype)
            edge_bias = (nx == 0 or nx == w - 1) + (ny == 0 or ny == h - 1)
            val = dist * 10 + edge_bias
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    else:
        best_val = None  # minimize distance to opponent
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = max(abs(nx - tx), abs(ny - ty))
            # Penalty for moving into being "surrounded" by obstacles/bounds
            neigh_block = 0
            for ix in (-1, 0, 1):
                for iy in (-1, 0, 1):
                    if ix == 0 and iy == 0:
                        continue
                    ax, ay = nx + ix, ny + iy
                    if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obs:
                        neigh_block += 1
            val = dist * 10 + neigh_block
            if best_val is None or val < best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]