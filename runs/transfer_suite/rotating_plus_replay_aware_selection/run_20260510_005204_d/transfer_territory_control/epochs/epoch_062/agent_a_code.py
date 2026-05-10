def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = []
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_terr.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    # Deterministically pick a small candidate set of targets
    center = (w - 1) / 2.0, (h - 1) / 2.0
    cand = []
    if unclaimed:
        # Prefer closer to center first, then deterministic by coordinates
        unclaimed_sorted = sorted(unclaimed, key=lambda t: (abs(t[0] - center[0]) + abs(t[1] - center[1]), t[1], t[0]))
        cand = unclaimed_sorted[:max(12, min(24, len(unclaimed_sorted)))]
    else:
        opp_sorted = sorted(opp_terr, key=lambda t: (md(sx, sy, t[0], t[1]), t[1], t[0]))
        cand = opp_sorted[:min(12, len(opp_sorted))]

    best = (1e18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # If stepping onto opponent territory is possible, give a big bias
        onto_opp = (nx, ny) in set(opp_terr) if opp_terr else False
        if onto_opp:
            score = -1000000 + md(nx, ny, ox, oy)  # deterministic
        else:
            # Choose target that maximizes (threatening) advantage: closer to us, farther from opponent
            best_threat = -1e18
            for tx, ty in cand:
                d_own = md(nx, ny, tx, ty)
                d_opp = md(ox, oy, tx, ty)
                # Prefer reducing our distance while increasing opponent separation; slight center bias
                center_bias = -(abs(tx - center[0]) + abs(ty - center[1])) * 0.02
                threat = (-d_own) + (0.75 * d_opp) + center_bias
                if threat > best_threat:
                    best_threat = threat
            score = -best_threat  # lower is better

        # Tie-break deterministically by (dx, dy)
        if score < best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]