def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                x, y = int(p["position"][0]), int(p["position"][1])
            elif "x" in p and "y" in p:
                x, y = int(p["x"]), int(p["y"])
            else:
                continue
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                x, y = int(r["position"][0]), int(r["position"][1])
            elif "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = -10**18
        for rx, ry in resources:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer stealing swing vs opponent, but also keep distance reasonable
            val = (opp_d - self_d) * 10 - self_d
            if val > my_best:
                my_best = val

        # Small tie-break: avoid edges only if it doesn't reduce target quality
        edge_pen = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_pen = 1
        total = my_best - edge_pen * 2

        if total > best_val:
            best_val = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]