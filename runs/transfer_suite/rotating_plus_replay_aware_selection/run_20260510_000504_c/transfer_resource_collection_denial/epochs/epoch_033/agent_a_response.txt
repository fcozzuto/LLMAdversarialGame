def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def clamp(x, a, b):
        return a if x < a else (b if x > b else x)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
            hit = (nx, ny) in obstacles
            best_adv = -10**9
            best_selfd = 10**9
            for rx, ry in resources:
                self_d = abs(rx - nx) + abs(ry - ny)
                opp_d = abs(rx - ox) + abs(ry - oy)
                adv = opp_d - self_d
                if adv > best_adv or (adv == best_adv and self_d < best_selfd):
                    best_adv, best_selfd = adv, self_d
            # Prefer higher advantage; avoid obstacles; among ties, move closer and then lexicographic.
            moves.append((hit, -best_adv, best_selfd, dx, dy))

    moves.sort()
    return [int(moves[0][3]), int(moves[0][4])]