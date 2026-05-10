def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neighbors8(cx, cy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if inb(nx, ny):
                    yield nx, ny

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (x, y)
    opp_pos = tuple(observation.get("opponent_position", [w - 1, h - 1]))

    # Prefer unclaimed cells adjacent to our territory (frontier expansion).
    frontier = []
    if selft:
        for sx, sy in selft:
            for nx, ny in neighbors8(sx, sy):
                if (nx, ny) in unclaimed and (nx, ny) not in obs:
                    frontier.append((nx, ny))
    targets = frontier if frontier else [c for c in unclaimed if c not in obs]

    if not targets:
        # Fallback: head toward opponent position while avoiding obstacles.
        tx, ty = opp_pos
    else:
        # Choose closest frontier/unclaimed; tie-break by safer direction away from opponent.
        tx, ty = min(
            targets,
            key=lambda c: (
                md(self_pos, c),
                md(c, opp_pos),
                c[0] * 9 + c[1],
            ),
        )

    # Pick move delta that gets us closer to chosen target (with obstacle avoidance).
    best = [0, 0]
    best_score = (10**9, 10**9, 10**9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # Small preference to avoid opponent territory unless it's the target pull.
            opp_pen = 1 if (nx, ny) in opp else 0
            score = (md((nx, ny), (tx, ty)), opp_pen, (dx, dy) != (0, 0))
            if score < best_score:
                best_score = score
                best = [dx, dy]
    return best