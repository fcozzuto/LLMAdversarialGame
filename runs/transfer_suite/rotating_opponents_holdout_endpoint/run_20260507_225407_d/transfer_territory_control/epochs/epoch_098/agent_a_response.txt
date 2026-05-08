def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_cells = set(tuple(c) for c in (observation.get("self_territory") or []))
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    target_cells = unclaimed if unclaimed else []
    if not target_cells:
        target_cells = list(opp_cells) if opp_cells else list(self_cells) if self_cells else [(int(cx), int(cy))]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    # Build a small "interest set": nearest few unclaimed cells (or fallback)
    tlist = target_cells
    if len(tlist) > 18:
        tlist = sorted(tlist, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))[:18]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cell = (nx, ny)
        if cell in self_cells:
            base = -2.0
        elif cell in opp_cells:
            base = 8.5  # flipping on entry
        elif cell in unclaimed:
            base = 5.0
        else:
            base = 0.5  # unknown/unlisted treated mildly

        # Prefer expanding from our boundary: adjacency to our territory
        adj = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            px, py = nx + ax, ny + ay
            if (px, py) in self_cells:
                adj += 1
        boundary = adj * 1.2

        # Center pressure: move toward center, avoid giving opponent too much
        dist_center = abs(nx - cx) + abs(ny - cy)
        center = -0.9 * dist_center

        # Contest pressure: pick nearby targets (unclaimed) deterministically
        nearest = 10**9
        for tx, ty in tlist:
            d = abs(tx - nx) + abs(ty - ny)
            if d < nearest:
                nearest = d
        target_drive = -0.55 * nearest

        # Keep away from opponent if we're not gaining (discourage suicidal flank)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        opp_pen = 0.0
        if cell not in opp_cells:
            opp_pen = 0.15 * (6 - min(dist_opp, 6))  # small penalty when close

        score = base + boundary + center + target_drive - opp_pen

        # Deterministic tie-break: prefer (0,0), then smallest dx, then smallest dy
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    # If all moves invalid (shouldn't), stay
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]