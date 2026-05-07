def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((o[0], o[1]))
        elif isinstance(o, dict) and "x" in o and "y" in o:
            obstacles.add((o["x"], o["y"]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((r[0], r[1]))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((r["position"][0], r["position"][1]))
            elif "x" in r and "y" in r:
                resources.append((r["x"], r["y"]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    # Target: nearest resource by Chebyshev distance (good for diagonals), tie-break by raw distance.
    if resources:
        def best_key(t):
            tx, ty = t
            return (max(abs(tx - sx), abs(ty - sy)), abs(tx - sx) + abs(ty - sy))
        target = min(resources, key=best_key)
        tx, ty = target

        def move_score(dx, dy):
            nx, ny = sx + dx, sy + dy
            d = max(abs(tx - nx), abs(ty - ny))
            # Prefer blocking the opponent by moving closer to the same resource than opponent.
            od = max(abs(tx - ox), abs(ty - oy))
            nd_od = max(abs(tx - nx), abs(ty - ny))
            return (d, nd_od - od, abs(nx - tx) + abs(ny - ty))
    else:
        # No visible resources: head to center while staying safe.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        def move_score(dx, dy):
            nx, ny = sx + dx, sy + dy
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            return (d, abs(nx - ox) + abs(ny - oy))

    # Deterministic tie-break: fixed ordering.
    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    move_set = set(moves)
    ordered_moves = [m for m in order if m in move_set] + [m for m in moves if m not in move_set]
    best = ordered_moves[0]
    best_s = None
    for m in ordered_moves:
        s = move_score(m[0], m[1])
        if best_s is None or s < best_s:
            best_s, best = s, m
    return [int(best[0]), int(best[1])]