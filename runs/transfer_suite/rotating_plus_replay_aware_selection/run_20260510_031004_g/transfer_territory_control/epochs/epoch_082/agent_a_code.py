def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        if cell in opp_terr:
            pri = 1000
        elif cell in unclaimed:
            pri = 800
        elif cell in self_terr:
            pri = 300
        else:
            pri = 0

        # Prefer expanding toward nearby unclaimed, but avoid walking deeper if center is over-claimed.
        # We add distance-to-nearest-unclaimed among a few closest cells using local density estimation:
        # evaluate nearest unclaimed in a small radius deterministically.
        near_u = 10**9
        for tx in (nx - 2, nx - 1, nx, nx + 1, nx + 2):
            for ty in (ny - 2, ny - 1, ny, ny + 1, ny + 2):
                if (tx, ty) in unclaimed:
                    d = abs(tx - nx) + abs(ty - ny)
                    if d < near_u:
                        near_u = d

        # If no unclaimed nearby, drift to frontier: toward opponent territory cells adjacent to unclaimed/self.
        if near_u == 10**9:
            near_o = 10**9
            for tx in (nx - 2, nx - 1, nx + 1, nx + 2):
                for ty in (ny - 2, ny - 1, ny + 1, ny + 2):
                    if (tx, ty) in opp_terr:
                        d = abs(tx - nx) + abs(ty - ny)
                        if d < near_o:
                            near_o = d
            near_u = near_o if near_o != 10**9 else 0

        center = abs(nx - cx) + abs(ny - cy)

        # Penalize staying still if there is any immediate capture/claim option around.
        immovable_pen = 1 if (dx == 0 and dy == 0) else 0

        # Key: maximize pri, then minimize near_u, then avoid deep center (opponent likes center), then prefer non-still.
        key = (pri, -near_u, -center, -immovable_pen, -abs(dx) - abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return [int(best[0]), int(best[1])]