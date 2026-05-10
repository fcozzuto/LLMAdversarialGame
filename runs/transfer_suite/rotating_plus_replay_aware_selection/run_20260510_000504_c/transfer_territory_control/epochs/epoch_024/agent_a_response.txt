def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neighbors8(x, y):
        out = []
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                out.append((nx, ny))
        return out

    def front_set(base):
        out = set()
        for (x, y) in base:
            for (nx, ny) in neighbors8(x, y):
                if (nx, ny) in unclaimed:
                    out.add((nx, ny))
        return out

    self_front = front_set(self_terr) if self_terr else set()
    opp_front = front_set(opp_terr) if opp_terr else set()

    def move_towards(tx, ty, prefer_enemy=False):
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Manhattan/Cheb distance; slight bias to reduce opponent access
            dist = max(abs(nx - tx), abs(ny - ty))
            bias = 0
            if prefer_enemy:
                # Prefer stepping closer to squares near our frontier lock (enemy front)
                bias = max(abs(nx - tx), abs(ny - ty)) - max(abs(sx - tx), abs(sy - ty))
            key = (dist, abs(nx - sx) + abs(ny - sy), bias, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Priority:
    # 1) Grab our nearest frontier cell (expansion).
    # 2) If none, cut off opponent by going to nearest opponent frontier cell (deny/contend).
    # 3) Otherwise, head to nearest unclaimed cell; then to center.
    if self_front:
        tx, ty = min(self_front, key=lambda p: (max(abs(p[0] - sx), abs(p[1] - sy)), p[0], p[1]))
        return move_towards(tx, ty, prefer_enemy=False)

    if opp_front:
        tx, ty = min(opp_front, key=lambda p: (max(abs(p[0] - sx), abs(p[1] - sy)), p[0], p[1]))
        return move_towards(tx, ty, prefer_enemy=True)

    if unclaimed:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = min(unclaimed, key=lambda p: (max(abs(p[0] - sx), abs(p[1] - sy)) + 0.25 * (abs(p[0] - cx) + abs(p[1] - cy)), p[0], p[1]))
        return move_towards(tx, ty, prefer_enemy=False)

    # Fallback: deterministic move towards center avoiding obstacles when possible
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return move_towards(cx, cy, prefer_enemy=False)